!
! LibAFCC - Library for auxiliary-function countercharge correction 
! Copyright (c) 2010-2011 I. Dabo
! This program is free software: you can redistribute it and/or modify
! it under the terms of the GNU General Public License as published by
! the Free Software Foundation.
!
! This program is distributed in the hope that it will be useful,
! but WITHOUT ANY WARRANTY; without even the implied warranty of
! MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
! GNU General Public License for more details.
!
! You should have received a copy of the GNU General Public License
! along with this program. See GPL/gpl-3.0.txt. 
! If not, see <http://www.gnu.org/licenses/>.
!
function besseli(x)
  !
  implicit none
  !
  real(8), intent(in) :: x
  real(8) :: besseli
  real(8), parameter :: eulergamma=0.5772156649015328606d0
  !
  interface
    !
    function cylharmseries(a0,b0,sigma,x)
      real(8), intent(in) :: a0,b0,sigma,x
      real(8) :: cylharmseries
    end function
    !
  end interface
  !
  besseli=cylharmseries(1.d0,0.d0,0.d0,x)
  !
end function besseli
